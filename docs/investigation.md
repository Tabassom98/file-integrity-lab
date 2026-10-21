# Investigating a change

A modified hash means that the bytes read differ from the trusted baseline. It does not mean a file is malicious. Updates, user edits, configuration management, and software installation can all explain changes.

In a real investigation, preserve the baseline and current artifact, establish how the baseline was created and protected, compare content with suitable tools, and correlate changes with authorized work and relevant endpoint logs. Do not automatically replace changed files without understanding operational effects.

Practice with the demo: create a baseline, edit settings.txt without changing its byte length, add a file, and remove another. Explain the three classifications. Rename a file and observe that it appears as an addition and removal. Keep dated notes of your own experiments and distinguish them from the AI-assisted starter.

An unchanged result is limited to monitored paths and content observed during this scan. It cannot establish that a system is uncompromised or that the baseline was trustworthy.
