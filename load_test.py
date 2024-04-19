from locust import HttpUser, between, task


class WebsiteUser(HttpUser):
    wait_time = between(5, 10)

    @task
    def load_page(self):
        self.client.get("/api/gastap/faucet/list/")
