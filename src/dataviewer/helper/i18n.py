from i18n_modern import I18nModern

from dataviewer.helper.config import settings
from dataviewer.helper.paths import get_path

i18n = I18nModern(settings.language, str(get_path(f"{settings.language}.yml", "locales")))
