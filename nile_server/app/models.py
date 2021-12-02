from app import db, ma


class Test(db.Model):
    __tablename__ = 'loadtest_tests'

    id = db.Column(db.Integer, primary_key=True)
    config = db.Column(db.String())
    locustfile = db.Column(db.String())
    start = db.Column(db.TIMESTAMP)
    end = db.Column(db.TIMESTAMP)
    workers = db.Column(db.Integer)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'config': self.config,
            'locustfile': self.locustfile,
            'start': self.start,
            'end': self.end,
            'workers': self.workers
        }


class TestSchema(ma.ModelSchema):
    class Meta:
        model = Test


class Request(db.Model):
    __tablename__ = 'loadtest_requests'

    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer)
    name = db.Column(db.String())
    request_timestamp = db.Column(db.TIMESTAMP)
    request_method = db.Column(db.String())
    request_length = db.Column(db.Integer)
    response_length = db.Column(db.Integer)
    response_time = db.Column(db.Float)
    status_code = db.Column(db.String())
    success = db.Column(db.Boolean)
    exception = db.Column(db.String())

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'test_id': self.test_id,
            'name': self.name,
            'request_timestamp': self.request_timestamp,
            'request_method': self.request_method,
            'request_length': self.request_length,
            'response_length': self.response_length,
            'response_time': self.response_time,
            'status_code': self.status_code,
            'success': self.success,
            'exception': self.exception
        }
        

class RequestSchema(ma.ModelSchema):
    class Meta:
        model = Request


class SystemMetric(db.Model):
    __tablename__ = 'loadtest_metrics'

    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer)
    system_name = db.Column(db.String)
    metric_name = db.Column(db.String())
    metric_timestamp = db.Column(db.TIMESTAMP)
    metric_value = db.Column(db.Float)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'test_id': self.test_id,
            'system_name': self.system_name,
            'metric_name': self.metric_name,
            'metric_timestamp': self.metric_timestamp,
            'metric_value': self.metric_value
        }


class SystemMetricSchema(ma.ModelSchema):
    class Meta:
        model = SystemMetric
