import click
from flask import Blueprint

from auth.models import db
from auth.services.roles import RoleService
from auth.services.users import UserService

bp = Blueprint('command', __name__)


@bp.cli.command('createsuperuser')
def create_super_user():
    """This is command for superuser creation"""
    prompt_suffix = ' >> '
    click.echo('Please enter superuser data')
    email = click.prompt('e-mail', type=str, prompt_suffix=prompt_suffix)
    first_name = click.prompt('First name', type=str,
                              prompt_suffix=prompt_suffix)
    last_name = click.prompt('Last name', type=str,
                             prompt_suffix=prompt_suffix)

    while True:
        password = click.prompt('Password', type=str, hide_input=True,
                                prompt_suffix=prompt_suffix)
        confirm_password = click.prompt('Please confirm password',
                                        type=str,
                                        hide_input=True,
                                        prompt_suffix=prompt_suffix)

        if password == confirm_password:
            break
        else:
            click.echo('Passwords does not match. Please try again.')

    click.echo('='*100)
    click.echo('Superuser data:')
    click.echo(f'e-mail: {email}')
    click.echo(f'First name: {first_name}')
    click.echo(f'Last name: {last_name}')

    if click.confirm('Do you want to create a superuser?'):
        click.echo(f'Well done! {password}')
        user_service = UserService(db)
        role_service = RoleService(db)
        if role_service.is_role_exists('admin') is False:
            role_service.create_role({
                'name': 'admin',
                'description': 'Superuser role'
            })

        super_user = user_service.create_super_user(email=email,
                                                    password=password,
                                                    first_name=first_name,
                                                    last_name=last_name)

        click.echo('SuperUser created successfully!')
        click.echo(super_user)
    else:
        click.echo('SuperUser creation canceled')
