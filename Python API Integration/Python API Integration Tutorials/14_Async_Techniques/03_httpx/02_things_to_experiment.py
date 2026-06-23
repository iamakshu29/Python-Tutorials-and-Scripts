# Make a request to a non-existent URL — what exception do you get?
# Set a very short timeout (0.001s) — watch it fail
# Make 20 requests with gather — measure vs sequential
# Make a request WITHOUT async with (don't close the client) — check for resource warnings
# Try streaming a large file — print chunk sizes to see how data arrives
