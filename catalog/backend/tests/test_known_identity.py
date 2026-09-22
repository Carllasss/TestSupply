from app.services.supplier_service import KnownIdentity, normalize_name, normalize_phone


def test_normalize_name_strips_legal_form_and_punctuation():
    assert normalize_name('ООО «Ромашка», лтд.') == normalize_name("Ромашка лтд")


def test_normalize_name_is_case_and_quote_insensitive():
    assert normalize_name('ООО "Ромашка"') == normalize_name("ооо «ромашка»")


def test_normalize_phone_converts_leading_8_to_7():
    assert normalize_phone("8 (900) 123-45-67") == normalize_phone("+7 900 123 45 67")


def test_normalize_phone_keeps_last_10_digits():
    assert normalize_phone("+7 900 123 45 67") == "9001234567"


def test_known_identity_matches_by_domain():
    identity = KnownIdentity(domains={"example.com"})
    assert identity.matches(domain="example.com")
    assert not identity.matches(domain="other.com")


def test_known_identity_matches_by_normalized_name():
    identity = KnownIdentity(names={normalize_name("Ромашка")})
    assert identity.matches(name='ООО «Ромашка»')
    assert not identity.matches(name="Другая компания")


def test_known_identity_matches_by_normalized_phone():
    identity = KnownIdentity(phones={normalize_phone("+7 900 123 45 67")})
    assert identity.matches(phone="8 (900) 123-45-67")
    assert not identity.matches(phone="+7 999 000 00 00")


def test_known_identity_matches_returns_false_when_nothing_given():
    identity = KnownIdentity(domains={"example.com"})
    assert not identity.matches()
