import pytest
from pathlib import Path
import sys

# Helper to verify imports works from test dir
sys.path.append(str(Path(__file__).parent.parent))

from scripts.migrators.react_hooks import ReactHooksMigrator

class TestReactHooksMigrator:
    def test_can_migrate(self):
        migrator = ReactHooksMigrator()
        assert migrator.can_migrate(Path("comp.jsx"))
        assert migrator.can_migrate(Path("comp.tsx"))
        assert not migrator.can_migrate(Path("script.py"))

    def test_migrate_class_component(self):
        migrator = ReactHooksMigrator()
        content = """
        import React, { Component } from 'react';
        class MyComp extends Component {
            render() {
                return <div>Hello {this.props.name}</div>;
            }
        }
        """
        new_content = migrator.migrate(content, Path("MyComp.jsx"))
        
        assert "class MyComp" not in new_content
        assert "const MyComp = (props) =>" in new_content
        assert "return <div>Hello {props.name}</div>" in new_content
        assert "useState" in new_content # It adds imports by default

    def test_migrate_no_change(self):
        migrator = ReactHooksMigrator()
        content = "const FuncComp = () => <div>Hello</div>;"
        new_content = migrator.migrate(content, Path("FuncComp.jsx"))
        assert content == new_content
