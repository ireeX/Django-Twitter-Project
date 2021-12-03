# Project Introduction
This is a twitter-like project. You can perform post and 
view tweets, follow and unfollow your friends.

## APIs:

['POST'] http://localhost/api/accounts/login/

['POST'] http://localhost/api/accounts/logout/

['GET'] http://localhost/api/accounts/login_status/

['POST'] http://localhost/api/accounts/signup/

['GET'] http://localhost/api/tweets/?user_id={user_id}

['POST'] http://localhost/api/tweets/?user_id={user_id}

['GET'] http://localhost/api/friendships/{user_id}/followings/

['GET'] http://localhost/api/friendships/{user_id}/followers/

['POST'] http://localhost/api/friendships/{user_id}/follow/

['POST'] http://localhost/api/friendships/{user_id}/unfollow/