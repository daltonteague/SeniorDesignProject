from locust import HttpLocust, TaskSet, task, between

from nile_test.integration import launch

launch("localhost:5000")


class UserBehavior(TaskSet):
    def on_start(self):
        """
        on_start is called when a Locust start before any task is scheduled
        """

    def on_stop(self):
        """ on_stop is called when the TaskSet is stopping """

    @task()
    def index(self):
        self.client.get("/")


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    wait_time = between(1, 3)
