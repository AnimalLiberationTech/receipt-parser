import os
from logging import getLogger, DEBUG

from azure.monitor.opentelemetry import configure_azure_monitor

LOG_FILE_NAME = "dev.log"


def set_logger():
    # logger = logging.getLogger("receipt-parser")
    # if os.getenv("ENV_NAME") == "dev":
    #     logger.setLevel(logging.DEBUG)
    #     handler = logging.FileHandler(LOG_FILE_NAME)
    #     handler.setLevel(logging.DEBUG)
    #     formatter = logging.Formatter(
    #         "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    #     )
    #     handler.setFormatter(formatter)
    #     logger.addHandler(handler)
    configure_azure_monitor(
        logger_name="receipt-parser",
        # connection_string="InstrumentationKey=14664268-6005-4043-bd09-55147ef57c05;IngestionEndpoint=https://westeurope-2.in.applicationinsights.azure.com/;LiveEndpoint=https://westeurope.livediagnostics.monitor.azure.com/;ApplicationId=941114f3-d80b-4be6-80db-bb9031543363",
    )

    logger = getLogger("receipt-parser")
    logger.setLevel(DEBUG)
    # logger_child = getLogger("receipt-parser.module")

    return logger
