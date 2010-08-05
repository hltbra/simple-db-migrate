#!/usr/bin/env python
# encoding: utf-8

from fudge import Fake, with_fakes, with_patched_object, \
                  clear_expectations, verify

import db_migrate.domain.migrations as migr
from db_migrate.domain.migrations import Migration
from db_migrate.domain.errors import *

test_path = "/tmp/20101010101010_doing_some_db_changes.migration"

def test_can_create_migration_model():
    migration = Migration(filepath=test_path)

    assert migration
    assert migration.filepath == test_path
    assert migration.filename == \
                "20101010101010_doing_some_db_changes.migration"
    assert migration.version == "20101010101010"
    assert migration.title == "doing_some_db_changes"

def test_creating_a_migration_with_an_invalid_filename_errors():
    try:
        migration = Migration(filepath="/tmp/config.ini")
    except InvalidMigrationFilenameError, err:
        assert str(err) == "The file '/tmp/config.ini' is not a migration and cannot be parsed. Migrations should have the .migration extension."
        return
    assert False, "Should not have gotten this far."

@with_fakes
@with_patched_object(migr, 'exists', Fake(callable=True))
def test_load_error_if_migration_does_not_exist():
    clear_expectations()

    migration = Migration(filepath=test_path)

    migr.exists.with_args(test_path).returns(False)

    try:
        migration.load()
    except MigrationFileDoesNotExistError, err:
        assert str(err) == "The migration at /tmp/20101010101010_doing_some_db_changes.migration does not exist", str(err)
        return

    assert False, "Should not have gotten this far"

@with_fakes
@with_patched_object(migr, 'exists', Fake(callable=True))
@with_patched_object(migr, 'codecs', Fake('codecs'))
def test_load_gets_the_file_contents_and_errors_if_file_has_no_SQL_UP():
    clear_expectations()

    expected_ups = ['up']
    expected_downs = ['down']

    migration = Migration(filepath=test_path)

    fake_file = Fake('file')
    migr.exists.with_args(test_path).returns(True)
    migr.codecs.expects('open') \
               .with_args(test_path, "rU", "utf-8") \
               .returns(fake_file)

    fake_file.expects('read').returns('''
SQL_DOWN = "some command"
''')
    fake_file.expects('close')

    try:
        migration.load()
    except InvalidMigrationFileError, err:
        assert str(err) == "Migration file at '/tmp/20101010101010_doing_some_db_changes.migration' it not well-formed. It should have both SQL_UP and SQL_DOWN variable assignments."
        return
    assert False, "Should not have gotten this far"

@with_fakes
@with_patched_object(migr, 'exists', Fake(callable=True))
@with_patched_object(migr, 'codecs', Fake('codecs'))
def test_load_gets_the_file_contents_and_errors_if_file_has_no_SQL_DOWN():
    clear_expectations()

    expected_ups = ['up']
    expected_downs = ['down']

    migration = Migration(filepath=test_path)

    fake_file = Fake('file')
    migr.exists.with_args(test_path).returns(True)
    migr.codecs.expects('open') \
               .with_args(test_path, "rU", "utf-8") \
               .returns(fake_file)

    fake_file.expects('read').returns('''
SQL_UP = "some command"
''')
    fake_file.expects('close')

    try:
        migration.load()
    except InvalidMigrationFileError, err:
        assert str(err) == "Migration file at '/tmp/20101010101010_doing_some_db_changes.migration' it not well-formed. It should have both SQL_UP and SQL_DOWN variable assignments."
        return
    assert False, "Should not have gotten this far"

def test_load_gets_the_file_contents_and_parses_ups_and_downs():
    assert False