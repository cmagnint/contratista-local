import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'find',
  standalone: true
})
export class FindPipe implements PipeTransform {
  /**
   * Finds an object in an array by its ID property
   * @param items Array of objects to search through
   * @param id The ID to search for
   * @param idField The name of the ID field (defaults to 'id')
   * @returns The matching object or undefined if not found
   */
  transform(items: any[] | null, id: any, idField: string = 'id'): any {
    if (!items || !id) {
      return null;
    }
    
    return items.find(item => item[idField] === id);
  }
}