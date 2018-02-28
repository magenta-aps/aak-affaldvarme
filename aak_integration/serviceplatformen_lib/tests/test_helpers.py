from udvidet_person_stamdata import validate_cprnr


def test_cpr_should_pass():

    cpr_value = "1234567890"

    # Expect to pass
    assert validate_cprnr(cpr_value)


def test_cpr_too_long_should_fail():

    cpr_value = "1234567890111"

    # Expect to fail
    assert not validate_cprnr(cpr_value)


def test_cpr_too_short_should_fail():

    cpr_value = "123456"

    # Expect to fail
    assert not validate_cprnr(cpr_value)


