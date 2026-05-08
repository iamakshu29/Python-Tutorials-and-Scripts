Types of Pagination strategies,
explaination 
How they workn internally
Used in where ?
2 place
Building logic while creating API
consuming logic while Consuming the API - Yield generator
real life example used...


Key Takeaway like

When building the API → add pagination params + return next_cursor or has_next in response
When consuming the API → use a generator with yield to lazily pull pages without loading everything into memory at once