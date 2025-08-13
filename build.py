import os
import sys
import subprocess
import shutil
import venv
from pathlib import Path


class BuildEnvironment:
    def __init__(self, env_dir: Path) -> None:
        self.env_dir = env_dir.resolve()
        self.bin_path = self.env_dir / 'Scripts' if os.name == 'nt' else self.env_dir / 'bin'
        self.python = str(self.bin_path / 'python')
        self.pyinstaller = str(self.bin_path / 'pyinstaller')
        self.pip = str(self.bin_path / 'pip')

    def create(self) -> None:
        """Create a clean virtual environment"""
        if self.env_dir.exists():
            print(f'Removing existing environment: {self.env_dir}')
            shutil.rmtree(self.env_dir)

        print(f'Creating virtual environment at: {self.env_dir}')
        venv.create(self.env_dir, with_pip=True)
        self.upgrade_pip()

    def upgrade_pip(self) -> None:
        """Upgrade pip in the virtual environment"""
        print('Upgrading pip in the virtual environment...')
        try:
            subprocess.check_call([self.pip, 'install', '--upgrade', 'pip'])

        except subprocess.CalledProcessError as e:
            print(f'Failed to upgrade pip: {e}')
            sys.exit(1)

    def install_dependencies(self, requirements: Path) -> None:
        """Install packages from requirements.txt"""
        if not requirements.exists():
            print(f'{requirements} not found. Skipping dependencies.')
            return

        print('Installing dependencies...')
        try:
            subprocess.check_call([self.pip, 'install', '-r', requirements])
            # Ensure PyInstaller is installed
            subprocess.check_call([self.pip, 'install', 'pyinstaller'])

        except subprocess.CalledProcessError as e:
            print(f'Dependency installation failed: {e}')
            sys.exit(1)

    def run_pyinstaller(self, output, entry_script, name, icon=None) -> None:
        """Build executable using PyInstaller in the virtual environment"""
        if output.exists():
            print(f'Removing existing build directory: {output}')
            shutil.rmtree(output)

        dist_path = output / 'dist'
        work_path = output / 'work'
        spec_path = output / 'spec'

        cmd = [
            self.pyinstaller,
            '--onefile',
            '--windowed',
            '--clean',
            '--noconfirm',
            '--name', name,
            '--distpath', str(dist_path),
            '--workpath', str(work_path),
            '--specpath', str(spec_path)
        ]

        if icon:
            cmd.extend(['--icon', str(icon)])
        cmd.append(str(entry_script))
        print('Building executable with command:')
        print(' '.join(cmd))

        try:
            subprocess.check_call(cmd)
            app_path = dist_path / name
            print(f'\nBuild successful! Executable: {str(app_path)}{'.exe' if os.name == 'nt' else ''}')

        except subprocess.CalledProcessError as e:
            print(f'Build failed: {e}')
            sys.exit(1)


if __name__ == "__main__":

    project_dir = Path(__file__).resolve().parent
    venv_dir = project_dir / '.venv'
    req_file = project_dir / 'requirements.txt'
    icon_file = project_dir / 'res' / 'ico' / 'app.icns'
    entry_point = project_dir / 'run.py'
    build_dir = project_dir / 'build'
    app_name = 'QAPAT'

    # Setup build environment
    builder = BuildEnvironment(venv_dir)

    # Create clean environment
    print('\n' + '=' * 50)
    print('Creating isolated build environment')
    print('=' * 50)
    builder.create()

    # Install dependencies
    print('\n' + '=' * 50)
    print('Installing dependencies')
    print('=' * 50)
    builder.install_dependencies(req_file)

    # Build executable
    print('\n' + '=' * 50)
    print('Building optimized executable')
    print('=' * 50)
    builder.run_pyinstaller(build_dir, entry_point, app_name, icon_file)

    print('\n' + '=' * 50)
    print('Build process completed!')
    print('=' * 50)
