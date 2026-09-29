from dj_design_system.data import GalleryParameter


basic_kwargs = {
    "quote": "To be or not to be",
    "slot__author": "William Shakespeare",
}

maximal_kwargs = {
    "quote": "To be or not to be, that is the question.",
    "slot__author": GalleryParameter(
        value="<strong>William Shakespeare</strong>",
        code='"<strong>William Shakespeare</strong>"',
    ),
    "slot__source": GalleryParameter(
        value="<cite>Hamlet</cite>", code='"<cite>Hamlet</cite>"'
    ),
}
