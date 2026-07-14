================
eea.genai.blocks
================
.. image:: https://ci.eionet.europa.eu/buildStatus/icon?job=eea/eea.genai.blocks/develop
  :target: https://ci.eionet.europa.eu/job/eea/job/eea.genai.blocks/job/develop/display/redirect
  :alt: Develop
.. image:: https://ci.eionet.europa.eu/buildStatus/icon?job=eea/eea.genai.blocks/master
  :target: https://ci.eionet.europa.eu/job/eea/job/eea.genai.blocks/job/master/display/redirect
  :alt: Master

LLM-powered Volto block generation and rewriting, built on the agentic
infrastructure of ``eea.genai.core``.

.. contents::

Main features
=============

1. ``generate_blocks(user_request, context, request, properties)`` —
   produce a full ``blocks`` + ``blocks_layout`` structure from a
   natural-language description (``blocks_generator`` agent).
2. ``generate_block(user_request, block_type=None, ...)`` — produce a
   single block (``blocks_generator_single`` agent).
3. ``rewrite_blocks(blocks, style=None, ...)`` and
   ``rewrite_block(block, style=None, ...)`` — rewrite text content in
   one or more blocks (``block_rewriter`` / ``block_rewriter_single``
   agents).
4. ``IBlockKnowledge`` named-utility registry — packages declare a
   block type's description, JSON schema, example, text extractor, and
   sanitizer. The agent's system prompt is built from these utilities.
5. ``BlocksKnowledgeSkill`` enricher — injects every registered block
   type's schema + example into the agent's system prompt.
6. ``BlocksContentProvider`` enricher — injects the current page's
   block text into the user prompt (batched ``IBlockKnowledge``
   lookups, no per-block ZCA queries).
7. Ships block knowledge for ``slate``, ``image``, ``columnsBlock``,
   ``tabs_block``. Custom block types register their own via
   ``<genai:blockKnowledge>``.
8. ``@llm-generate-blocks`` and ``@llm-rewrite-blocks`` REST endpoints.

Install
=======

- Add ``eea.genai.blocks`` to your ``requirements.txt``.
- Install the GenericSetup profile.
- The four default agents are registered automatically via ZCML and can
  be overridden by name via the core control panel ``agents_json``.

Adding a new block type
=======================

In your addon's ``configure.zcml``::

    <genai:blockKnowledge
        block_type="my_block"
        title="My Block"
        class=".knowledge.MyBlockKnowledge"
    />

In ``knowledge.py``::

    from eea.genai.blocks.interfaces import BlockKnowledge

    class MyBlockKnowledge(BlockKnowledge):
        description = "Describe what the block is for"
        schema = '{"@type": "my_block", "value": "..."}'
        example = '{"@type": "my_block", "value": "hello"}'

        def text_extractor(self, block):
            return block.get("value", "")

        def block_sanitizer(self, block):
            return block  # post-LLM cleanup, return canonical dict

Generation/rewriting agents will pick up the new block type
automatically — no change to agent config required.

Copyright and license
=====================

The Initial Owner of the Original Code is European Environment Agency (EEA).
All Rights Reserved.

All contributions to this package are property of their respective authors,
and are covered by the same license.

The eea.genai.blocks is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 2 of the License, or (at your
option) any later version.

Secret Scanning
===============

This repository uses the Betterleaks GitHub Action to scan the current
repository content on every push and pull request. The scan uses the rules in
``.gitleaks.toml`` and uploads a ``betterleaks-report`` artifact when a finding
is detected.

If the optional SMTP secrets are configured, failed scans also send an email to
the last commit committer. The workflow expects these repository or
organization secrets:

- ``SMTP_URL``
- ``SMTP_PORT`` (optional, defaults to ``25``)
- ``SMTP_EMAIL``
- ``SMTP_PASSWORD`` (optional if the SMTP server does not require authentication)

Port ``465`` is sent with direct TLS; other ports use the default SMTP
handshake. The email includes a short finding summary from the redacted
Betterleaks report, including the redacted matched line from each finding.

There are three common outcomes:

1. Everything is OK. The ``Betterleaks / Scan for secrets`` check is green and
   no action is needed. Regular references to runtime values are OK, for example::

     token_from_cookie = request.cookies.get("auth_token")

2. A real secret was found. The check is red and the workflow log asks you to
   download the ``betterleaks-report`` artifact. Open the artifact from the
   GitHub Actions run and check the reported file, line and rule. Remove the
   committed value, move it to the proper secret store, and rotate it if it was
   exposed. A report entry looks like this::

     {
       "RuleID": "secret-literal-assignment",
       "File": "src/config.py",
       "StartLine": 12,
       "Secret": "[REDACTED]"
     }

3. The finding is a false positive. Keep the value only if it is clearly not
   sensitive, such as a test fixture, placeholder, or public example. Add
   ``betterleaks:allow`` on the same line and include a short explanation in the
   pull request::

     test_password = "admin"  #betterleaks:allow

Do not add ``betterleaks:allow`` to real credentials.
