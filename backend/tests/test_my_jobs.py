def register_and_login(
    client,
    name,
    email,
    password,
):
    register_response = client.post(
        "/auth/register",
        json={
            "name": name,
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}",
    }


def create_job(
    client,
    headers,
    title,
    location,
    budget,
):
    response = client.post(
        "/jobs/",
        headers=headers,
        json={
            "title": title,
            "description": (
                "Need help completing this real work."
            ),
            "location": location,
            "budget": budget,
        },
    )

    assert response.status_code == 201

    return response.json()


def test_get_my_jobs(client):
    headers = register_and_login(
        client,
        "Manish",
        "myjobs-manish@example.com",
        "TestPassword123",
    )

    create_job(
        client,
        headers,
        "Fix Electrical Wiring",
        "Bhopal",
        2500,
    )

    create_job(
        client,
        headers,
        "Install Ceiling Fan",
        "Bhopal",
        1800,
    )

    response = client.get(
        "/jobs/mine",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    assert all(
        job["customer_id"] == 1
        for job in data
    )


def test_get_my_jobs_excludes_other_users_jobs(client):
    manish_headers = register_and_login(
        client,
        "Manish",
        "myjobs-manish-2@example.com",
        "TestPassword123",
    )

    create_job(
        client,
        manish_headers,
        "Manish Electrical Work",
        "Bhopal",
        2500,
    )

    rahul_headers = register_and_login(
        client,
        "Rahul",
        "myjobs-rahul@example.com",
        "TestPassword456",
    )

    response = client.get(
        "/jobs/mine",
        headers=rahul_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 0


def test_get_my_jobs_requires_authentication(client):
    response = client.get(
        "/jobs/mine",
    )

    assert response.status_code == 401