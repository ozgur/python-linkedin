# -*- coding: utf-8 -*-

class LinkedInError(Exception):
    pass


class LinkedInBadRequestError(LinkedInError):
    pass


class LinkedInUnauthorizedError(LinkedInError):
    pass


class LinkedInPaymentRequiredError(LinkedInError):
    pass


class LinkedInNotFoundError(LinkedInError):
    pass


class LinkedInConflictError(LinkedInError):
    pass


class LinkedInForbiddenError(LinkedInError):
    pass


class LinkedInInternalServiceError(LinkedInError):
    pass


ERROR_CODE_EXCEPTION_MAPPING = {
    400: LinkedInBadRequestError,
    401: LinkedInUnauthorizedError,
    402: LinkedInPaymentRequiredError,
    403: LinkedInForbiddenError,
    404: LinkedInNotFoundError,
    409: LinkedInForbiddenError,
    500: LinkedInInternalServiceError}


def get_exception_for_error_code(error_code):
    return ERROR_CODE_EXCEPTION_MAPPING.get(error_code, LinkedInError)
