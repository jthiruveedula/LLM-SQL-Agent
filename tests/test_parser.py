from llm_sql_agent.parser import parse_and_validate, referenced_tables


def test_valid_transpile_snowflake_to_bigquery():
    sql = "SELECT id, name FROM customers WHERE id = 1"
    result = parse_and_validate(sql, "snowflake", "bigquery")
    assert result.is_valid
    assert "SELECT" in result.transpiled_sql


def test_syntax_error_is_captured_not_raised():
    result = parse_and_validate("SELEC 1", "snowflake", "bigquery")
    assert not result.is_valid
    assert result.syntax_errors


def test_referenced_tables():
    sql = "SELECT o.id FROM orders o JOIN customers c ON o.customer_id = c.id"
    tables = referenced_tables(sql, "snowflake")
    assert "orders" in " ".join(tables).lower()
    assert "customers" in " ".join(tables).lower()
