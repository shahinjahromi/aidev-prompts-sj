import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { EventEmitter } from '@angular/core';
import { Input } from '@angular/core';
import { Output } from '@angular/core';

@Component({
  selector: 'app-support-modal',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './support-modal.component.html',
  styleUrl: './support-modal.component.scss'
})
export class SupportModalComponent {
  @Input() open = false;
  @Output() closeRequested = new EventEmitter<void>();

  close(): void {
    this.closeRequested.emit();
  }
}
