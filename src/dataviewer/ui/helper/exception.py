from nicegui import app, ui


@app.on_page_exception
def file_not_found(exception: Exception):
    if not isinstance(exception, FileNotFoundError):
        raise exception
    text = (
        "<br>A file you're trying to load does not exist *yet* on the server."
        "<br><br>It likely is one of the files that should be automatically downloaded."
        "If you just started the program for the first time i may have fetched the file by now."
        "In that case a **page reload** might also fix the problem."
        "<br><br>If reloading doesn't help:"
        "<br>Please review your cloud files, your config, check /files on the server and read the logs. "
    )
    ui.query(".nicegui-content").classes(
        "pt-10 min-h-full bg-dark w-full no-scroll sm:h-[calc(100vh-56px)]"
    )  # remove default padding from site
    ui.code(exception.args[0], language="sh").classes("bg-secondary")
    ui.markdown(text).classes("p-10 pt-2 h-dvh mx-auto text-justify text-base/6 antialiasing text-gray-300 max-w-180")
