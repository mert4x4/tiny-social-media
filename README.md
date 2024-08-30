# Tiny Social Media

This is a small-scale social media project that includes server, client, and database components. Users can register, log in, and have their passwords stored in the database using encryption. Once logged in, users can post text updates, which are visible to all other users. Additionally, users can comment on any post.

The entire project runs within Docker containers.
## Features

- **User Registration and Login**: Secure authentication with encrypted passwords.
- **Post Updates**: Users can share text posts visible to all other users.
- **Commenting**: Users can comment on any post.

## Getting Started

To build and run the project, use the following command:

```bash
docker-compose up --build
