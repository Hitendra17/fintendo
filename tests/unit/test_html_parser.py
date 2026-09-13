from fintendo.data.html_parser import HTMLParser, ParsedPage


def test_extracts_title_and_readable_text():
    html = """
    <html>
        <head>
            <title>Market Update</title>
            <script>alert("malicious")</script>
            <style>.hidden { display: none; }</style>
        </head>
        <body>
            <nav>Navigation</nav>
            <main>
                <h1>Market Update</h1>
                <p>Revenue increased during the quarter.</p>
            </main>
            <footer>Footer</footer>
        </body>
    </html>
    """

    parser = HTMLParser()
    result = parser.parse(html)

    assert isinstance(result, ParsedPage)
    assert result.title == "Market Update"
    assert "Revenue increased during the quarter." in result.text
    assert "malicious" not in result.text
    assert "Navigation" not in result.text
    assert "Footer" not in result.text


def test_rejects_empty_html():
    parser = HTMLParser()

    try:
        parser.parse("   ")
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == "HTML content must not be empty."


def test_rejects_html_without_readable_text():
    parser = HTMLParser()

    html = """
    <html>
        <head><title>Empty</title></head>
        <body>
            <script>something()</script>
        </body>
    </html>
    """

    try:
        parser.parse(html)
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == "No readable text found in HTML content."