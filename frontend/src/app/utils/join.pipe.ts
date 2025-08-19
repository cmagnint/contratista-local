import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'join',
  standalone: true
})
export class JoinPipe implements PipeTransform {
  transform(array: any[], separator: string = ', '): string {
    if (!Array.isArray(array)) {
      return array;
    }
    return array.join(separator);
  }
}