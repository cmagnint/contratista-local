import { Pipe, PipeTransform } from "@angular/core";
import { __values } from "tslib";

@Pipe({
    name: 'newline',
    standalone: true,
})
export class NewLinePipe implements PipeTransform {
    transform(value: string): string {
        return value.replace(/\n/g,'<br/>');
    }
} 