"""
"""

import os
import distutils
import logging
import yaml

_LOGGER = logging.getLogger(__name__)


def join_model_path(config):
    """Construct model path."""
    config.MODEL_PATH = os.path.join(config.MODEL_DIR, config.MODEL_FILE)


def join_w2v_model_path(config):
    """Construct a word2vec model path."""
    config.W2V_MODEL_PATH = os.path.join(config.MODEL_DIR, config.W2V_MODEL_FILE)


def check_or_create_model_dir(config):
    """Check if model dir exists and create if not."""
    if not os.path.exists(config.MODEL_DIR):
        os.mkdir(config.MODEL_DIR)

class Borg(object):
    __shared_state = {}

    def __init__(self):
        self.__dict__ = self.__shared_state

    def __str__(self):
        return self.state


class Configuration(Borg):
    """
    Configuration object.
    
    Properties which names are all caps are used for configuration of the application.

    If the name contains _CALLABLE suffix, it is called after the environment variables are loaded
    """
    FACT_STORE_URL = ""
    # One of the storage backends available in storage/ dir
    STORAGE_BACKEND = "local"
    # Location of local data
    # A directory where trained models will be stored
    MODEL_DIR = "./models/"
    MODE_DIR_CALLABLE = check_or_create_model_dir
    # Name of the file where SOM model will be stored TODO: move to model config
    MODEL_FILE = "SOM.model"
    # Name of the file where W2V model will be stored TODO: move to model config
    W2V_MODEL_FILE = "W2V.model"
    MODEL_PATH_CALLABLE = join_model_path
    MODEL_PATH = ""
    W2V_MODEL_PATH_CALLABLE = join_w2v_model_path
    W2V_MODEL_PATH = ""
    MODEL_STORE= ""
    MODEL_STORE_PATH = 'anomaly-detection/models/'
    # Number of seconds specifying how far to the past to go to load log entries for training TODO: move to es storage backend
    TRAIN_TIME_SPAN = 900
    # Maximum number of entries for training loaded from backend storage
    TRAIN_MAX_ENTRIES = 315448
    # Number of SOM training iterations TODO: move to model config
    TRAIN_ITERATIONS = 315448
    # If true, re-traing the models
    TRAIN_UPDATE_MODEL = False
    # Set the window size for word2Vec training
    TRAIN_WINDOW = 5
    # Set the length of the encoded log vectors
    TRAIN_VECTOR_LENGTH = 25
    #number of jobs to use to parallelize the training, should match cpu resource limit
    PARALLELISM = 2

    # Threshold used to decide whether an entry is an anomaly
    INFER_ANOMALY_THRESHOLD = 3.1
    # Number of seconds specifying how far in the past to go to load log entries for inference TODO: move to es storage backend
    INFER_TIME_SPAN = 60
    # Number of inferences before retraining the models
    INFER_LOOPS = 10
    # Maximum number of entries to be loaded for inference
    INFER_MAX_ENTRIES = 78862

    # S3 credentials for storing model up to s3 post training.
    S3_KEY = ""
    S3_SECRET = ""
    S3_HOST = ""
    S3_BUCKET = ""
    # local test dataset
    LS_INPUT_PATH = ""
    # Name of local results data
    LS_OUTPUT_PATH =""

    prefix = "LAD"

    def __init__(self, prefix=None, config_yaml=None):
        """Initialize configuration."""
        if config_yaml is not None:
            # TODO: Open YAML File and load the configurations in here.
            with open(config_yaml) as f:
                yaml_data = yaml.load(f, Loader=yaml.FullLoader)
                for prop in self.__class__.__dict__.keys():
                    attr = getattr(self, prop)
                    if prop.isupper() and prop.endswith("_CALLABLE") \
                            and callable(attr):
                        attr()
                    elif prop.isupper() and prop in list(yaml_data.keys()):
                        self.set_property(prop, yaml_data[prop])
                        # self.__setattr__(prop, yaml_data[prop])
        else:
            self.storage = None
            if prefix:
                self.prefix = prefix
            self.load()

    def load(self):
        """Load the configuration."""
        _LOGGER.info("Loading %s" % self.__class__.__name__)
        self.load_from_env()

    def load_from_env(self):
        """Load the configuration from environment."""
        for prop in self.__class__.__dict__.keys():
            if not prop.isupper():
                continue
            env = "%s_%s" % (self.prefix, prop)
            val = os.environ.get(env)
            self.set_property(prop, val)

        for prop in self.__class__.__dict__.keys():
            attr = getattr(self, prop)
            if prop.isupper() and prop.endswith("_CALLABLE") \
                    and callable(attr):
                attr()

    def set_property(self,  prop, val):
        typ = type(getattr(self, prop))
        if val:

            if typ is int:
                setattr(self, prop, int(val))
            elif typ is float:
                setattr(self, prop, float(val))
            elif typ is str:
                setattr(self, prop, str(val))
            elif typ is bool:
                if type(val) is bool:
                    setattr(self, prop, val)
                else:
                    setattr(self, prop, bool(distutils.util.strtobool(val)))
            else:
                raise Exception("Incorrect type for %s (%s) loaded " % (prop, typ))
