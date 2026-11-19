import { useEffect, useRef, useState } from "react";
import { cn } from "@/lib/utils";
import { Field, FieldGroup, FieldLabel } from "@/components/ui/field";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

type ResearchField = {
  name: "domain" | "arm" | "endpoint";
  label: string;
  value: string;
  options: { id: string; label: string }[];
};

type Props = {
  fields: ResearchField[];
  kind: "domain" | "challenge";
};

export default function ResearchControls({ fields, kind }: Props) {
  const form = useRef<HTMLFormElement>(null);
  const [hydrated, setHydrated] = useState(false);
  useEffect(() => setHydrated(true), []);

  return (
    <form
      ref={form}
      hidden={!hydrated}
      className={cn({ "domain-control": kind === "domain", "challenge-controls": kind === "challenge" })}
      aria-label={kind === "domain" ? "Choose a task domain" : "Choose the challenge and outcome"}
      onSubmit={(event) => event.preventDefault()}
    >
      <FieldGroup className={cn("grid gap-3", kind === "challenge" && "sm:grid-cols-2")}>
        {fields.map((field) => (
          <Field
            key={field.name}
            orientation={kind === "domain" ? "horizontal" : "vertical"}
            className={cn("gap-2", kind === "domain" && "flex-wrap gap-x-3")}
          >
            <FieldLabel id={`result-${field.name}-label`} htmlFor={`result-${field.name}`}>
              {field.label}
            </FieldLabel>
            <Select
              name={field.name}
              defaultValue={field.value}
              items={field.options.map((option) => ({ label: option.label, value: option.id }))}
              onValueChange={(value) => {
                const explorer = form.current?.closest<HTMLElement>("[data-findings-explorer]");
                if (!explorer || typeof value !== "string") return;
                // Retain the latest value even if the chart script is still loading.
                explorer.dataset[field.name] = value;
                explorer.dispatchEvent(new Event("research-filter-change"));
              }}
            >
              <SelectTrigger
                id={`result-${field.name}`}
                aria-labelledby={`result-${field.name}-label`}
                className={cn("w-full", kind === "domain" && "w-40")}
              >
                <SelectValue placeholder={field.label} />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  {field.options.map((option) => (
                    <SelectItem key={option.id} value={option.id}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectGroup>
              </SelectContent>
            </Select>
          </Field>
        ))}
      </FieldGroup>
    </form>
  );
}
