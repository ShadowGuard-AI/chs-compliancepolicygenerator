#!/usr/bin/env python3

import argparse
import yaml
import jinja2
import logging
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class CompliancePolicyGenerator:
    """
    Generates configuration hardening scripts based on compliance policies.
    """

    def __init__(self, compliance_standard, config_file, output_file, platform):
        """
        Initializes the CompliancePolicyGenerator.

        Args:
            compliance_standard (str): The name of the compliance standard (e.g., CIS).
            config_file (str): The path to the YAML configuration file.
            output_file (str): The path to the output script file.
            platform (str): The target platform (e.g., linux, windows).
        """
        self.compliance_standard = compliance_standard
        self.config_file = config_file
        self.output_file = output_file
        self.platform = platform
        self.config = None
        self.template = None

    def load_config(self):
        """
        Loads the YAML configuration file.
        """
        try:
            with open(self.config_file, 'r') as f:
                self.config = yaml.safe_load(f)
            logging.info(f"Configuration loaded from {self.config_file}")
        except FileNotFoundError:
            logging.error(f"Configuration file not found: {self.config_file}")
            raise
        except yaml.YAMLError as e:
            logging.error(f"Error parsing YAML configuration: {e}")
            raise

    def validate_config(self):
        """
        Validates the loaded configuration.
        """
        if not isinstance(self.config, dict):
            logging.error("Invalid configuration format. Expected a dictionary.")
            raise ValueError("Invalid configuration format")

        # The templates loop over config.policies and nothing else. A
        # config without that key rendered a script with a shebang and
        # no hardening in it, and the run still reported success, which
        # is the worst outcome a compliance generator can produce.
        if not self.config.get('policies'):
            logging.error("Configuration has no 'policies' to generate from.")
            raise ValueError("Configuration must define a non-empty 'policies' list")

    def load_template(self):
        """
        Loads the Jinja2 template file.
        """
        template_path = f"templates/{self.platform}/{self.compliance_standard}.j2"
        try:
            # The loader root is the working directory, not this file's
            # folder, on purpose: the caller supplies the template tree
            # for their own standards, so templates live with the call.
            env = jinja2.Environment(loader=jinja2.FileSystemLoader('.'))
            self.template = env.get_template(template_path)
            logging.info(f"Template loaded from {template_path}")
        except jinja2.exceptions.TemplateNotFound:
            logging.error(f"Template not found: {template_path}")
            raise
        except Exception as e:
            logging.error(f"Error loading template: {e}")
            raise

    def generate_script(self):
        """
        Generates the hardening script using the configuration and template.
        """
        try:
            # Jinja2's default undefined renders as empty text instead
            # of failing, so a policy key the template names slightly
            # differently than the config writes a blank into the
            # script at that spot, and the run still reports success.
            # The generated script needs reading, not just generating.
            rendered_script = self.template.render(config=self.config)
            # Config values land in the output exactly as written,
            # unsanitised, because the output is a script and the
            # template decides where values go. That makes the config
            # file trusted input: a service name carrying shell syntax
            # is carried straight into the generated script.
            with open(self.output_file, 'w') as f:
                f.write(rendered_script)
            logging.info(f"Script generated successfully: {self.output_file}")
        except Exception as e:
            logging.error(f"Error generating script: {e}")
            raise

    def run(self):
        """
        Runs the entire script generation process.
        """
        try:
            self.load_config()
            self.validate_config()
            self.load_template()
            self.generate_script()
        except Exception as e:
            logging.error(f"Script generation failed: {e}")
            sys.exit(1)


def setup_argparse():
    """
    Sets up the command-line argument parser.
    """
    parser = argparse.ArgumentParser(description='Generates configuration hardening scripts based on compliance policies.')
    parser.add_argument('--compliance-standard', '-c', required=True, help='The compliance standard (e.g., CIS)')
    parser.add_argument('--config-file', '-f', required=True, help='The path to the YAML configuration file')
    parser.add_argument('--output-file', '-o', required=True, help='The path to the output script file')
    parser.add_argument('--platform', '-p', required=True, help='The target platform (e.g., linux, windows)')
    return parser.parse_args()


def main():
    """
    Main function to execute the script.
    """
    args = setup_argparse()

    try:
        generator = CompliancePolicyGenerator(
            args.compliance_standard,
            args.config_file,
            args.output_file,
            args.platform
        )
        generator.run()
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Example Usage:
    # Create 'config.yaml' and 'templates/linux/CIS.j2' (or equivalent) first.
    # Run: python main.py --compliance-standard CIS --config-file config.yaml --output-file hardening.sh --platform linux
    #
    # Example config.yaml:
    # policies:
    #   - name: Disable unnecessary services
    #     services:
    #       - atd
    #       - cups
    #
    # Example templates/linux/CIS.j2
    # #!/bin/bash
    # {% for policy in config.policies %}
    # # Policy: {{ policy.name }}
    # {% if policy.services %}
    # {% for service in policy.services %}
    # systemctl disable {{ service }}
    # systemctl stop {{ service }}
    # {% endfor %}
    # {% endif %}
    # {% endfor %}

    main()