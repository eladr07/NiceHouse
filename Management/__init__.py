def init_logging():
    import settings, logging.config
    logging.config.fileConfig(settings.SITE_ROOT + 'logging.conf')

logInitDone=False
if not logInitDone:
    logInitDone = True
    init_logging()
