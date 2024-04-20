from locust import HttpUser, between, task


class WebsiteUser(HttpUser):
    wait_time = between(5, 10)

    @task
    def load_page(self):
        # self.client.get("/api/gastap/faucet/list/")
        # self.client.get("/api/tokentap/get-valid-chains/")
        self.client.get("/api/gastap/settings/")
