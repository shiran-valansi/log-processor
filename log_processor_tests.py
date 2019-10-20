if __name__ == "__main__":
    import doctest
    import log_processor

    result = doctest.testmod(log_processor)
    if not result.failed:
        print("ALL TESTS PASSED!")
