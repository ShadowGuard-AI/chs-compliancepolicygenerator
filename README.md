![Banner](banner.png)

# chs-CompliancePolicyGenerator
Generates platform-specific hardening scripts (for example shell scripts or Ansible playbooks) from a YAML configuration file, using a Jinja2 template for the chosen compliance standard and platform. The configuration must define a non-empty `policies` list. The template is read from `templates/<platform>/<standard>.j2` relative to the working directory, so the caller supplies the template tree for their own standards.

## Install
`git clone https://github.com/ShadowGuard-AI/chs-compliancepolicygenerator`

## Usage
`python3 main.py --compliance-standard CIS --config-file config.yaml --output-file hardening.sh --platform linux`

## Parameters
- `-h`: Show help message and exit
- `-c`, `--compliance-standard`: The compliance standard (for example CIS). Required.
- `-f`, `--config-file`: The path to the YAML configuration file. Required.
- `-o`, `--output-file`: The path to the output script file. Required.
- `-p`, `--platform`: The target platform (for example linux, windows). Required.

## Verified behavior
- The parameter list above is taken from the argument parser in `main.py`, and `main.py` passes `py_compile`.
- A live run was not completed in this wave: the `jinja2` package is not installed here and installs are not permitted in this wave, so `--help` and a generation run both stop at that missing import. Install `jinja2` and `PyYAML` from `requirements.txt` before running.
- A configuration without a non-empty `policies` list fails the run instead of producing an empty script.

## License
See LICENSE.
