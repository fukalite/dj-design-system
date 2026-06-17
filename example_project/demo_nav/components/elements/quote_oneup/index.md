# Quote One-Up

The `quote_oneup` component is a complex block component that showcases slots and rich HTML content.

## Basic Usage

```gallery
{% quote_oneup "To be or not to be" %}
{% slot "author" %}Shakespeare{% endslot %}
{% endquote_oneup %}
```

## Complex Usage

```canvas
{% quote_oneup "To be or not to be, that is the question." %}
{% slot "author" %}<strong>William Shakespeare</strong>{% endslot %}
{% slot "source" %}<cite>Hamlet</cite>{% endslot %}
{% endquote_oneup %}
```
