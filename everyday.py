from models import User
import config as cfg


for user in User.select():
    user.balance += cfg.everyday_money
    user.save()