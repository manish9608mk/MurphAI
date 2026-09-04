def register_and_login(
    client,
    name,
    email,
    password,
):
    register_response = client.post(
        "/users/",
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
        "Authorization": f"Bearer {token}"
    }


def create_job(client, headers):
    response = client.post(
        "/jobs/",
        headers=headers,
        json={
            "title": "Fix Electrical Wiring",
            "description": "Need an electrician to repair wiring in my house.",
            "location": "Bhopal",
            "budget": 2500,
        },
    )

    assert response.status_code == 201

    return response.json()


def test_create_job(client):
    headers = register_and_login(
        client,
        "Manish",
        "manish@example.com",
        "TestPassword123",
    )

    response = client.post(
        "/jobs/",
        headers=headers,
        json={
            "title": "Fix Electrical Wiring",
            "description": "Need an electrician to repair wiring in my house.",
            "location": "Bhopal",
            "budget": 2500,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] == 1
    assert data["title"] == "Fix Electrical Wiring"
    assert data["description"] == (
        "Need an electrician to repair wiring in my house."
    )
    assert data["location"] == "Bhopal"
    assert data["budget"] == 2500
    assert data["status"] == "open"
    assert data["customer_id"] == 1


def test_get_jobs(client):
    headers = register_and_login(
        client,
        "Manish",
        "manish@example.com",
        "TestPassword123",
    )

    create_job(client, headers)

    response = client.get(
        "/jobs/",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["title"] == "Fix Electrical Wiring"


def test_get_single_job(client):
    headers = register_and_login(
        client,
        "Manish",
        "manish@example.com",
        "TestPassword123",
    )

    job = create_job(client, headers)

    response = client.get(
        f"/jobs/{job['id']}",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == job["id"]
    assert data["customer_id"] == 1


def test_update_own_job(client):
    headers = register_and_login(
        client,
        "Manish",
        "manish@example.com",
        "TestPassword123",
    )

    job = create_job(client, headers)

    response = client.put(
        f"/jobs/{job['id']}",
        headers=headers,
        json={
            "title": "Updated Electrical Job",
            "description": "Updated description for electrical repair work.",
            "location": "Indore",
            "budget": 3000,
            "status": "open",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Updated Electrical Job"
    assert data["location"] == "Indore"
    assert data["budget"] == 3000


def test_cannot_update_other_users_job(client):
    manish_headers = register_and_login(
        client,
        "Manish",
        "manish@example.com",
        "TestPassword123",
    )

    create_job(client, manish_headers)

    rahul_headers = register_and_login(
        client,
        "Rahul",
        "rahul@example.com",
        "TestPassword123",
    )

    response = client.put(
        "/jobs/1",
        headers=rahul_headers,
        json={
            "title": "Hacked Job",
            "description": "Trying to modify another user's job.",
            "location": "Delhi",
            "budget": 1,
            "status": "open",
        },
    )

    assert response.status_code == 403

    data = response.json()

    assert data["detail"] == (
        "You are not allowed to update this job"
    )


def test_delete_own_job(client):
    headers = register_and_login(
        client,
        "Manish",
        "manish@example.com",
        "TestPassword123",
    )

    job = create_job(client, headers)

    response = client.delete(
        f"/jobs/{job['id']}",
        headers=headers,
    )

    assert response.status_code == 204

    response = client.get(
        f"/jobs/{job['id']}",
        headers=headers,
    )

    assert response.status_code == 404


def test_cannot_delete_other_users_job(client):
    manish_headers = register_and_login(
        client,
        "Manish",
        "manish@example.com",
        "TestPassword123",
    )

    create_job(client, manish_headers)

    rahul_headers = register_and_login(
        client,
        "Rahul",
        "rahul@example.com",
        "TestPassword123",
    )

    response = client.delete(
        "/jobs/1",
        headers=rahul_headers,
    )

    assert response.status_code == 403

    data = response.json()

    assert data["detail"] == (
        "You are not allowed to delete this job"
    )


def test_job_not_found(client):
    headers = register_and_login(
        client,
        "Manish",
        "manish@example.com",
        "TestPassword123",
    )

    response = client.get(
        "/jobs/999",
        headers=headers,
    )

    assert response.status_code == 404


def test_create_job_requires_authentication(client):
    response = client.post(
        "/jobs/",
        json={
            "title": "Fix Electrical Wiring",
            "description": "Need an electrician to repair wiring in my house.",
            "location": "Bhopal",
            "budget": 2500,
        },
    )

    assert response.status_code == 401


def test_get_jobs_requires_authentication(client):
    response = client.get(
        "/jobs/",
    )

    assert response.status_code == 401


def test_get_single_job_requires_authentication(client):
    headers = register_and_login(
        client,
        "Manish",
        "manish@example.com",
        "TestPassword123",
    )

    job = create_job(client, headers)

    response = client.get(
        f"/jobs/{job['id']}",
    )

    assert response.status_code == 401


def test_other_user_can_view_job(client):
    manish_headers = register_and_login(
        client,
        "Manish",
        "manish@example.com",
        "TestPassword123",
    )

    job = create_job(
        client,
        manish_headers,
    )

    rahul_headers = register_and_login(
        client,
        "Rahul",
        "rahul@example.com",
        "TestPassword123",
    )

    response = client.get(
        f"/jobs/{job['id']}",
        headers=rahul_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == job["id"]
    assert data["customer_id"] == 1