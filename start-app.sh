#!/bin/bash

# Wait until PostgreSQL started and listens on port 5432.
while [ -z "$( psql -qt -c "\dt adcirc_save_points" | cut -d \| -f 2 )" ]; do
  echo 'Waiting for PostgreSQL to start ...'
  sleep 1
done
echo 'PostgreSQL started.'

# Start server.
echo 'Starting server...'
DATABASE_URL=postgres://localhost:5432/postgres \
python app.py
