def get_kotlin_type(column_type: str, is_not_null):
    nullable = "? = null" if not is_not_null else ""
    kotlin_type = "String"
    match column_type:
        case "INTEGER":
            kotlin_type = "Integer"
        case "REAL":
            kotlin_type = "Double"

    return "{}{}".format(kotlin_type, nullable)
