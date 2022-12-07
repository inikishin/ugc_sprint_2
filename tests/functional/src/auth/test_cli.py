def test_createsuperuser(auth_runner):
    result = auth_runner.invoke(
        args='command createsuperuser',
        input='\n'.join(['test_cli@email.com', 'first cli', 'admin', 'test', 'test', 'y']))

    assert result.exit_code == 0
    assert 'SuperUser created successfully!' in result.output
