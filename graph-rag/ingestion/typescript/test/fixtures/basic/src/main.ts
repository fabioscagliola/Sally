export interface Contract {
  value: string;
}

export class Base {
  protected value: string = "base";
}

export class Child extends Base implements Contract {
  value = "child";

  run(input: Contract): string {
    return helper(input.value);
  }
}

export function helper(value: string): string {
  return value;
}

export const namedArrow = (value: string): string => helper(value);
const anonymous = ["x"].map((value) => value);
void anonymous;
