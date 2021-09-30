from lplangid import language_classifier as lc, count_utils as cu

# This is the very simplest way to share data structures between tests.
# I dare say it can become unsafe if you do bad things. So please don't.
# Or move to some kind of fixture structure. One that works with PyCharm and isn't too fiddly.
ALL_TERM_RANKS, ALL_CHAR_WEIGHTS = lc.prepare_scoring_tables()

TEST_TEXTS = [("This is English", "en"),
              ("Esto es español", "es"),
              ("Can you please thank you", "en"),
              ("Hi", "en"),
              ("Hello", "en"),
              ("No , I'm presently a Vodafone customer", "en"),
              ("Gracias", "es"),
              ("24 pls", "en"),
              ("Obrigada, bom dia!", "pt"),
              ("I agree", "en"),
              ("吸尘器", "zh"),
              ("掃除機が壊れた", "ja"),
              ("书", "zh"),
              ("本", "ja"),
              ("転送が完了するまでしばらくお待ちください", "ja"),
              #  ("Me interesa", "es"),  # This would be nice to catch and correct!
              ("Please", "en"),
              ("안녕하세요? 안녕하세요?", "ko"),
              ("123", None),
              ("ᵔ", None),
              ("ᵔ is a hat", "en"),
              ("呗", "zh"),
              ("アンケートを終了いたします。お問い合わせありがとうございました。", "ja"),
              ("wuglmkqufd mgackxzrfk ydcxscavcb kvbtwygmew cicdrlnrck pqrawbsrsc jjmwwxpwem exouqfmkuj wuugakutqw "
               "nyfjakojtm vwnhvanazz fogkjhovxw grdhnmejzk hgquytxtzk xscfjlmozv pbnxfqmshr afzglkacyb lsfwcbrqcf",
               None),
              ("<!EncryptedText ,,, even if followed", None),
              ("displayText more text", None),
              ("kindly update me once done", "en"),
              ("http://go.microsoft.com/fwlink/?LinkID=267510&clcid=0x409", None),
              ("国内感染確認１万1543人 (クルーズ船除く) 新型コロナ", "ja"),
              ("क्या हाल है", "hi"),
              ("saya bisa bicara bahasa", "id"),
              ('Metadata\n-----------\n\n{"splus":{"os":"android"}}\n\n	', None),
              ('https://downloads.anywhere.com is enough to block classification', None),
              ('I have questions about all..', 'en'),
              ('Tôi đã đăng ký được 25 ngày. Sao đến giờ vẫn chưa có phản hồi', 'vi'),
              ('por favor desactiva mi tarjeta', 'es')
              ]


def test_language_classifier_cases():
    for text in TEST_TEXTS:
        winner = lc.get_winner(ALL_TERM_RANKS, ALL_CHAR_WEIGHTS, text[0])
        assert winner == text[1], f"Expected {text[1]} instead of {winner} for \"{text[0]}\""


def test_language_classifier_cases2():
    classifier = lc.RRCLanguageClassifier.default_instance()
    for text in TEST_TEXTS:
        winner = classifier.get_winner(text[0])
        assert winner == text[1], f"Expected {text[1]} instead of {winner} for \"{text[0]}\""


def test_classifier_instance():
    classifier = lc.RRCLanguageClassifier.default_instance()
    assert classifier.get_winner("This is English") == "en"
    assert classifier.get_winner_score("This is English")[0] == "en"
    assert classifier.get_language_scores("This is English")[0][0] == "en"


def test_get_winner_score_for_digit():
    ws = lc.get_winner_score(ALL_TERM_RANKS, ALL_CHAR_WEIGHTS, '1')
    assert ws == (None, 0.0)


def test_get_winner_margin():
    winner1, margin = lc.get_winner_margin(ALL_TERM_RANKS, ALL_CHAR_WEIGHTS, 'no')
    winner2, score = lc.get_winner_score(ALL_TERM_RANKS, ALL_CHAR_WEIGHTS, 'no')
    assert winner1 == winner2 == 'it'
    assert margin < score
    winner2, margin2 = lc.get_winner_margin(ALL_TERM_RANKS, ALL_CHAR_WEIGHTS, '안녕하세요')
    assert margin2 > margin


def test_invert_char_tables():
    lang_to_char_weights = {"en": {"e": 0.4, "a": 0.3, "t": 0.3}, "id": {"a": 0.4, "e": 0.3, "n": 0.3}}
    char_to_lang_weights = lc.invert_char_tables(lang_to_char_weights)
    assert char_to_lang_weights["a"][0][0] == "id"
    assert char_to_lang_weights["e"][0][0] == "en"
    assert len(char_to_lang_weights["t"]) == 1


def _test_large_precision():
    """Remove _ from the beginning of this and ask Dominic for test data if you want to try this for testing changes.

    Used initially to compare softmax with L1-norm for character score distribution.

    With L1:      Attempted 99670, correct with 95210. (P: 95.55, R: 95.21, F: 95.37)
    With SoftMax: Attempted 99665, correct with 95169. (P: 95.45, R: 95.17, F: 95.33)
    So they're almost identical, L1 slightly better on this dataset.

    After adding LivePerson terms into term ranks: Attempted 96397, correct with 94164. (P: 97.69, R: 0.9416, F: 95.89)
    """
    test_data = open("/Users/dwiddows/Data/wikipedia_sample.tsv")
    import csv
    reader = csv.reader(test_data, delimiter="\t")
    attempted = 0
    correct = 0
    total = 0
    for lang, text in reader:
        total += 1
        winner = lc.get_winner(ALL_TERM_RANKS, ALL_CHAR_WEIGHTS, text)
        if winner:
            attempted += 1
        if attempted and winner == lang:
            correct += 1
    print(f"Attempted: {attempted}, Correct: {correct}, Out of total: {total}")
    precision, recall, f_measure = cu.precision_recall_f(total, attempted, correct)
    print(f"Precision: {precision}, Recall: {recall}, F-measure: {f_measure}")


def test_sr_hr():
    """Shows that text from a Serbian radio station gets classified as Croatian,
    because of the vernacular latin orthography."""
    test_sr = """FEMISAN A
    NAJBOLJE JUTRO
    07-09h
    Svakog radnog dana od 07h do 09h prvu, drugu i trecu jutarnju kafu sa Vama pije ekipa Najboljeg Jutra.
    Zapocnite jutro uz najvece hitove za celu Srbiju, uz zanimljive teme i puno smeha.
    """
    assert lc.get_winner(ALL_TERM_RANKS, ALL_CHAR_WEIGHTS, test_sr) == "hr"


def test_break():
    # Test to see if this causes an alert if we try to push it to github.
    assert False
