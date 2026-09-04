# ============================================================
# Worker Skills Tests
# ============================================================
#
# These tests verify that:
#
# 1. A worker can add a skill.
# 2. A worker can view their skills.
# 3. A worker can remove a skill.
# 4. The same skill cannot be added twice.
# 5. Another user cannot modify someone else's skills.
# 6. Skills can be shared by different workers.
# 7. Proper errors are returned for invalid requests.
#
# ============================================================


from backend.app.core.security import create_access_token
from backend.app.models.user import User


# ------------------------------------------------------------
# Helper: Create a test user
# ------------------------------------------------------------
#
# We create users directly in the test database.
#
# This keeps our tests independent from the real database.
#
def create_test_user(
    db,
    name: str,
    email: str,
):
    user = User(
        name=name,
        email=email,
        password_hash="test-password-hash",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user.id


# ------------------------------------------------------------
# Helper: Create authentication headers
# ------------------------------------------------------------
#
# Our API requires authentication.
#
# This creates a JWT token for the given user.
#
def auth_headers(user_id: int):
    token = create_access_token(user_id)

    return {
        "Authorization": f"Bearer {token}",
    }


# ------------------------------------------------------------
# Helper: Create a worker
# ------------------------------------------------------------
#
# Most skill tests need a worker first.
#
# Instead of repeating worker creation code
# in every test, we create a small helper.
#
def create_worker(
    client,
    user_id: int,
):
    response = client.post(
        "/workers/",
        headers=auth_headers(user_id),
        json={
            "bio": "Experienced electrician",
            "location": "Bhopal",
            "experience_years": 5,
            "is_available": True,
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


# ============================================================
# TEST 1
# Worker can add a skill
# ============================================================

def test_worker_can_add_skill(client, db):
    # Create a user.
    user_id = create_test_user(
        db,
        "Skill Worker One",
        "skillworker1@example.com",
    )

    # Create the worker profile.
    worker_id = create_worker(
        client,
        user_id,
    )

    # Add a skill to the worker.
    response = client.post(
        f"/workers/{worker_id}/skills",
        headers=auth_headers(user_id),
        json={
            "name": "Electrician",
        },
    )

    # Skill creation should succeed.
    assert response.status_code == 201

    data = response.json()

    # Check that the skill was created correctly.
    assert data["name"] == "Electrician"

    # A database ID should be returned.
    assert data["id"] > 0


# ============================================================
# TEST 2
# Worker can view their skills
# ============================================================

def test_worker_can_view_skills(client, db):
    user_id = create_test_user(
        db,
        "Skill Worker Two",
        "skillworker2@example.com",
    )

    worker_id = create_worker(
        client,
        user_id,
    )

    # Add two skills.
    client.post(
        f"/workers/{worker_id}/skills",
        headers=auth_headers(user_id),
        json={
            "name": "Electrician",
        },
    )

    client.post(
        f"/workers/{worker_id}/skills",
        headers=auth_headers(user_id),
        json={
            "name": "Wiring",
        },
    )

    # Get all skills of this worker.
    response = client.get(
        f"/workers/{worker_id}/skills",
        headers=auth_headers(user_id),
    )

    assert response.status_code == 200

    data = response.json()

    # Worker should have exactly two skills.
    assert len(data) == 2

    # Check the skill names.
    skill_names = {
        skill["name"]
        for skill in data
    }

    assert skill_names == {
        "Electrician",
        "Wiring",
    }


# ============================================================
# TEST 3
# Worker can remove a skill
# ============================================================

def test_worker_can_remove_skill(client, db):
    user_id = create_test_user(
        db,
        "Skill Worker Three",
        "skillworker3@example.com",
    )

    worker_id = create_worker(
        client,
        user_id,
    )

    # First add a skill.
    create_response = client.post(
        f"/workers/{worker_id}/skills",
        headers=auth_headers(user_id),
        json={
            "name": "Plumbing",
        },
    )

    assert create_response.status_code == 201

    skill_id = create_response.json()["id"]

    # Now remove the skill.
    response = client.delete(
        f"/workers/{worker_id}/skills/{skill_id}",
        headers=auth_headers(user_id),
    )

    assert response.status_code == 204

    # Verify that the worker has no skills left.
    get_response = client.get(
        f"/workers/{worker_id}/skills",
        headers=auth_headers(user_id),
    )

    assert get_response.status_code == 200
    assert get_response.json() == []


# ============================================================
# TEST 4
# Same skill cannot be added twice
# ============================================================

def test_worker_cannot_add_same_skill_twice(client, db):
    user_id = create_test_user(
        db,
        "Skill Worker Four",
        "skillworker4@example.com",
    )

    worker_id = create_worker(
        client,
        user_id,
    )

    payload = {
        "name": "Electrician",
    }

    # First addition should succeed.
    first_response = client.post(
        f"/workers/{worker_id}/skills",
        headers=auth_headers(user_id),
        json=payload,
    )

    # Second addition should fail.
    second_response = client.post(
        f"/workers/{worker_id}/skills",
        headers=auth_headers(user_id),
        json=payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409

    assert (
        second_response.json()["detail"]
        == "Worker already has this skill"
    )


# ============================================================
# TEST 5
# Skill names are treated case-insensitively
# ============================================================

def test_skill_name_is_case_insensitive(client, db):
    user_id = create_test_user(
        db,
        "Skill Worker Five",
        "skillworker5@example.com",
    )

    worker_id = create_worker(
        client,
        user_id,
    )

    # Add "Electrician".
    first_response = client.post(
        f"/workers/{worker_id}/skills",
        headers=auth_headers(user_id),
        json={
            "name": "Electrician",
        },
    )

    # Try adding "ELECTRICIAN".
    second_response = client.post(
        f"/workers/{worker_id}/skills",
        headers=auth_headers(user_id),
        json={
            "name": "ELECTRICIAN",
        },
    )

    assert first_response.status_code == 201

    # It should recognize that both names
    # represent the same skill.
    assert second_response.status_code == 409


# ============================================================
# TEST 6
# Another worker can use the same skill
# ============================================================

def test_same_skill_can_belong_to_multiple_workers(
    client,
    db,
):
    # Create first user.
    first_user_id = create_test_user(
        db,
        "Skill Worker Six",
        "skillworker6@example.com",
    )

    # Create second user.
    second_user_id = create_test_user(
        db,
        "Skill Worker Seven",
        "skillworker7@example.com",
    )

    first_worker_id = create_worker(
        client,
        first_user_id,
    )

    second_worker_id = create_worker(
        client,
        second_user_id,
    )

    # First worker adds Electrician.
    first_response = client.post(
        f"/workers/{first_worker_id}/skills",
        headers=auth_headers(first_user_id),
        json={
            "name": "Electrician",
        },
    )

    # Second worker also adds Electrician.
    second_response = client.post(
        f"/workers/{second_worker_id}/skills",
        headers=auth_headers(second_user_id),
        json={
            "name": "Electrician",
        },
    )

    # Both should succeed.
    assert first_response.status_code == 201
    assert second_response.status_code == 201

    # Both workers should have the skill.
    first_skills = client.get(
        f"/workers/{first_worker_id}/skills",
        headers=auth_headers(first_user_id),
    )

    second_skills = client.get(
        f"/workers/{second_worker_id}/skills",
        headers=auth_headers(second_user_id),
    )

    assert first_skills.status_code == 200
    assert second_skills.status_code == 200

    assert first_skills.json()[0]["name"] == "Electrician"
    assert second_skills.json()[0]["name"] == "Electrician"


# ============================================================
# TEST 7
# Another user cannot add a skill to my worker
# ============================================================

def test_other_user_cannot_add_skill(
    client,
    db,
):
    # Worker owner.
    owner_id = create_test_user(
        db,
        "Skill Owner",
        "skillowner@example.com",
    )

    # Different user.
    other_user_id = create_test_user(
        db,
        "Skill Attacker",
        "skillattacker@example.com",
    )

    worker_id = create_worker(
        client,
        owner_id,
    )

    # Other user tries to add a skill.
    response = client.post(
        f"/workers/{worker_id}/skills",
        headers=auth_headers(other_user_id),
        json={
            "name": "Hacking",
        },
    )

    assert response.status_code == 403

    assert (
        response.json()["detail"]
        == "You are not allowed to add skills to this worker profile"
    )


# ============================================================
# TEST 8
# Another user cannot remove my skill
# ============================================================

def test_other_user_cannot_remove_skill(
    client,
    db,
):
    owner_id = create_test_user(
        db,
        "Skill Owner Two",
        "skillowner2@example.com",
    )

    other_user_id = create_test_user(
        db,
        "Skill Attacker Two",
        "skillattacker2@example.com",
    )

    worker_id = create_worker(
        client,
        owner_id,
    )

    # Owner adds a skill.
    create_response = client.post(
        f"/workers/{worker_id}/skills",
        headers=auth_headers(owner_id),
        json={
            "name": "Plumbing",
        },
    )

    skill_id = create_response.json()["id"]

    # Other user tries to remove it.
    response = client.delete(
        f"/workers/{worker_id}/skills/{skill_id}",
        headers=auth_headers(other_user_id),
    )

    assert response.status_code == 403

    assert (
        response.json()["detail"]
        == "You are not allowed to remove skills from this worker profile"
    )


# ============================================================
# TEST 9
# Anyone authenticated can view worker skills
# ============================================================

def test_other_user_can_view_worker_skills(
    client,
    db,
):
    owner_id = create_test_user(
        db,
        "Skill Owner Three",
        "skillowner3@example.com",
    )

    viewer_id = create_test_user(
        db,
        "Skill Viewer",
        "skillviewer@example.com",
    )

    worker_id = create_worker(
        client,
        owner_id,
    )

    # Owner adds a skill.
    client.post(
        f"/workers/{worker_id}/skills",
        headers=auth_headers(owner_id),
        json={
            "name": "AC Repair",
        },
    )

    # Different authenticated user views the skills.
    response = client.get(
        f"/workers/{worker_id}/skills",
        headers=auth_headers(viewer_id),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "AC Repair"


# ============================================================
# TEST 10
# Unauthenticated user cannot view skills
# ============================================================

def test_get_worker_skills_requires_authentication(
    client,
):
    response = client.get(
        "/workers/1/skills",
    )

    assert response.status_code == 401


# ============================================================
# TEST 11
# Unauthenticated user cannot add a skill
# ============================================================

def test_add_worker_skill_requires_authentication(
    client,
):
    response = client.post(
        "/workers/1/skills",
        json={
            "name": "Electrician",
        },
    )

    assert response.status_code == 401


# ============================================================
# TEST 12
# Unauthenticated user cannot remove a skill
# ============================================================

def test_remove_worker_skill_requires_authentication(
    client,
):
    response = client.delete(
        "/workers/1/skills/1",
    )

    assert response.status_code == 401


# ============================================================
# TEST 13
# Worker does not exist
# ============================================================

def test_worker_not_found_for_skills(
    client,
    db,
):
    user_id = create_test_user(
        db,
        "Skill Worker Eight",
        "skillworker8@example.com",
    )

    response = client.get(
        "/workers/999999/skills",
        headers=auth_headers(user_id),
    )

    assert response.status_code == 404

    assert (
        response.json()["detail"]
        == "Worker not found"
    )


# ============================================================
# TEST 14
# Cannot remove a skill that the worker does not have
# ============================================================

def test_worker_skill_not_found(
    client,
    db,
):
    user_id = create_test_user(
        db,
        "Skill Worker Nine",
        "skillworker9@example.com",
    )

    worker_id = create_worker(
        client,
        user_id,
    )

    response = client.delete(
        f"/workers/{worker_id}/skills/999999",
        headers=auth_headers(user_id),
    )

    assert response.status_code == 404

    assert (
        response.json()["detail"]
        == "Worker skill not found"
    )