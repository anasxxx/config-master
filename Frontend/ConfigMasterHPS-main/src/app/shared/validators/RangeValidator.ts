// range-validator.ts
import { Directive } from '@angular/core';
import { AbstractControl, NG_VALIDATORS, ValidationErrors, Validator } from '@angular/forms';

@Directive({
  selector: '[appTrancheRangeValidator]',
  providers: [{ 
    provide: NG_VALIDATORS,
    useExisting: TrancheRangeValidatorDirective,
    multi: true
  }]
})
export class TrancheRangeValidatorDirective implements Validator {
  validate(control: AbstractControl): ValidationErrors | null {
    const minCtrl = control.get('trancheMin');
    const maxCtrl = control.get('trancheMax');
    
    if (!minCtrl || !maxCtrl) return null;

    // Only validate when both fields have values
    if (!minCtrl.value || !maxCtrl.value) return null;

    const errors: ValidationErrors = {};
    const min = minCtrl.value as string;
    const max = maxCtrl.value as string;

    // Numeric validation
    const minNum = Number(min);
    const maxNum = Number(max);
    if (isNaN(minNum) || isNaN(maxNum)) {
      errors['invalidNumber'] = true;
    } else if (maxNum <= minNum) {
      errors['endRangeLessThanStart'] = true;
    }

    // 16-digit numeric length validation
    const digitRegex = /^\d{16}$/;
    if (!digitRegex.test(min) || !digitRegex.test(max)) {
      errors['mustBe16Digits'] = true;
    }

    // Length validation: ensure both inputs same length (still useful for other lengths)
    if (min.length !== max.length) {
      errors['rangeLengthMismatch'] = true;
    }

    return Object.keys(errors).length ? errors : null;
  }
}
