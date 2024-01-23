terraform {
	required_providers {
		aws = {
			source = "hashicorp/aws"
		}
	}

	backend "remote" {
		hostname = "app.terraform.io"
		organization = "Datasciencetest"

		workspaces {
			name = "api-traefik-kub-2024-DEV"
		}
	}
}
