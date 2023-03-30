-- ----------------------------
-- Trigger of update_project_percent_completed
-- ----------------------------
CREATE OR REPLACE FUNCTION update_project_percent_completed()
RETURNS TRIGGER AS $$
DECLARE
    total_tasks INTEGER;
    completed_tasks INTEGER;
    coefficient_completed DECIMAL(5,2);
BEGIN
    SELECT COUNT(*) INTO total_tasks FROM public."Task" WHERE public."Task".project_id = NEW.project_id;
    SELECT COUNT(*) INTO completed_tasks FROM public."Task" WHERE public."Task".project_id = NEW.project_id AND public."Task".done = true;
    IF total_tasks = 0 THEN
        coefficient_completed := 0.0;
    ELSE
        coefficient_completed := ROUND(completed_tasks::numeric / total_tasks::numeric, 2);
    END IF;
    UPDATE public."Project" SET percent_completed = coefficient_completed WHERE public."Project".id = NEW.project_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER task_update_percent_completed_trigger
AFTER INSERT OR UPDATE OR DELETE ON public."Task"
FOR EACH ROW
EXECUTE FUNCTION update_project_percent_completed();
