# (major, minor, patch, prerelease)

VERSION = (0, 0, 6, "")
__shortversion__ = '.'.join(map(str, VERSION[:3]))
__version__ = '.'.join(map(str, VERSION[:3])) + "".join(VERSION[3:])

__package_name__ = 'pyqubo'
__contact_names__ = 'Recruit Communications Co., Ltd.'
__contact_emails__ = 'rco_pyqubo@ml.cocorou.jp'
__homepage__ = 'https://pyqubo.readthedocs.io/en/latest/'
__repository_url__ = 'https://github.com/recruit-communications/pyqubo'
__download_url__ = 'https://github.com/recruit-communications/pyqubo'
__description__ = 'PyQUBO allows you to create QUBOs or Ising models from mathematical expressions.'
__license__ = 'Apache 2.0'
__keywords__ = 'QUBO, quantum annealing, annealing machine, ising model, optimization'
