from flask import jsonify


class ResponseFactory:
    """Uniform JSON envelope for operation endpoints.

    Lives under app/models because it's the response-side counterpart of
    CRUDMixin: routes build responses from it the same way they build
    records from the mixin.
    """

    @staticmethod
    def _build(status_code, message=None, data=None, **extra):
        payload = {"success": 200 <= status_code < 300}
        if message is not None:
            payload["message"] = message
        if data is not None:
            payload["data"] = data
        payload.update(extra)
        return jsonify(payload), status_code

    @classmethod
    def ok(cls, data=None, message="OK"):
        return cls._build(200, message=message, data=data)

    @classmethod
    def created(cls, data=None, message="Created"):
        return cls._build(201, message=message, data=data)

    @classmethod
    def bad_request(cls, message="Bad request"):
        return cls._build(400, message=message)

    @classmethod
    def unauthorized(cls, message="Unauthorized"):
        return cls._build(401, message=message)

    @classmethod
    def forbidden(cls, message="Forbidden"):
        return cls._build(403, message=message)

    @classmethod
    def not_found(cls, message="Not found"):
        return cls._build(404, message=message)

    @classmethod
    def conflict(cls, message="Conflict"):
        return cls._build(409, message=message)

    @classmethod
    def error(cls, message="Internal server error"):
        return cls._build(500, message=message)
