#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
from flask_migrate import Migrate,MigrateCommand
from flask_script import Manager,Shell
from app import create_app, db
from app.models import User, Role, Permission, Post
from sqlalchemy.pool import manage
from test.test_basics import BasicsTestCase 

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Permission=Permission, Post=Post)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().loadTestsFromTestCase(BasicsTestCase)
    unittest.TextTestRunner(verbosity=2).run(tests)
    
if __name__ == "__main__":
    manager.run()