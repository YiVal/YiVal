---
sidebar_position: 8
---
# Logger

## `TokenLogger`

### Introduction

### Class Definition

#### Description

   The `TokenLogger` class is a singleton class designed to keep track of token usage. As a singleton, it ensures that there's only one instance of the logger throughout the runtime of the application. The class provides methods to log token usage, retrieve the current usage, and reset the counter.

#### Methods

### `log`

- Logs or adds the number of tokens used to the current usage counter.
- Parameters:
    - `tokens(int)`: The number of tokens to add to the current usage counter.

### `get_current_usage`

- Retrieves the current token usage.
- Returns:
    - `int`: The token usage of the current operation.

### `reset`

- Resets the current token usage counter to zero.

### Example

  To utilize the `TokenLogger`:

**Initialization**: Since it's a singleton, you don't need to worry about multiple instances.

```Python
   logger = TokenLogger()
```

**Logging Tokens**: You can add tokens to the counter.

```Python
   logger.log(150)
```

**Retrieving Usage**: Get the current token usage.

```Python
     current_usage = logger.get_current_usage()
     print(current_usage)  # This will print 150
```

**Resetting the Counter**: If you want to reset the token usage:

```Python
  logger.reset()
```
