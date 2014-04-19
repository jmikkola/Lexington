Lexington
=========

A python web framework centred around dependency injection

This is a proof of concept project at the moment. Play around with it, but
don't expect it to be close to production ready.

# Design tennants

- Work silently, fail noisily
- Detect errors early
- No global state
- Test everything
- Don't hide the implementation

# Using

```
source setup_env
cd examples/
python hello_app.py
```

# Contributing

Send me a pull request.


# TODO

- Clean up path module
- Add exception handling and allow registering custom exception handlers
- Improve distribution system (add a setup.py?)
- Split internal and external modules
