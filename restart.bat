heroku ps:scale web=0
heroku stop web.1
heroku pg:killall
heroku ps:scale web=1
