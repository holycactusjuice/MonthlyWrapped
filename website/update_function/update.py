from models import User, users


def update_db():
    user_documents = users.find()

    for user_document in user_documents:
        user = User.from_document(user_document)
        user.update_listen_data()
