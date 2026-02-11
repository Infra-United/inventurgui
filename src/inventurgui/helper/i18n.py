from i18n_modern import I18nModern

from inventurgui.helper.config import settings
from inventurgui.helper.paths import get_path

i18n = I18nModern(settings.language, str(get_path(f"{settings.language}.yml", "locales")))